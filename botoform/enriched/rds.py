from datetime import datetime

from nested_lookup import nested_lookup

from ..util import reflect_attrs, generate_password


class EnrichedRds(object):

    def __init__(self, evpc):
        # save the EnrichedVpc object.
        self.evpc = evpc

        # capture a list of this classes attributes before reflecting.
        self.self_attrs = dir(self)

        # reflect all connection attributes into EnrichedRds.
        reflect_attrs(self, self.evpc.boto.rds, self.self_attrs)

    def get_all_db_descriptions(self):
        """return a list of all db description dictionaries."""
        return self.describe_db_instances()["DBInstances"]

    def _related_db_filter(self, db_description):
        """return True if db related to VPC else False."""
        return db_description["DBSubnetGroup"]["VpcId"] == self.evpc.vpc.id

    def get_related_db_descriptions(self):
        """return a list of db description dictionaries related to this VPC."""
        return filter(self._related_db_filter, self.get_all_db_descriptions())

    def get_related_db_ids(self):
        """return a list of db instance identifiers related to this VPC."""
        return nested_lookup("DBInstanceIdentifier", self.get_related_db_descriptions())

    def get_related_db_endpoints(self):
        """return a list of cache cluster dns endpoints related to this VPC"""
        return nested_lookup("Endpoint", self.get_related_db_descriptions())

    def get_related_connection_data(self):
        """return a dictionary of DB Connection data related to this VPC"""
        db_connection_data = {}
        for description in self.get_related_db_descriptions():
            db_connection_data[description["DBInstanceIdentifier"]] = {
                "host": description["Endpoint"]["Address"],
                "port": description["Endpoint"]["Port"],
                "master_username": description["MasterUsername"],
                "database_name": description.get("DBName", None),
                "engine": description["Engine"],
                "engine_version": description["EngineVersion"],
            }
        return db_connection_data

    def wait_for_related_dbs(self, waiter_name, db_ids=None):
        """wait for related dbs to transition to desired state."""
        if db_ids is None:
            db_ids = self.get_related_db_ids()
        for db_id in db_ids:
            self.get_waiter(waiter_name).wait(DBInstanceIdentifier=db_id)

    def delete_related_db_instances(self, db_ids=None, skip_snapshot=False):
        """
        delete all RDS DB instances and subnet groups related to this VPC.

        rds_ids:
            optional list of rds_ids (names) to delete instead.
        """
        date = datetime.now().strftime("%Y-%m-%d-%H%m")
        descriptions = self.get_related_db_descriptions()
        related_db_ids = nested_lookup("DBInstanceIdentifier", descriptions)

        if db_ids is None:
            db_ids = related_db_ids
        else:
            # We make sure db_ids are part of this VPC.
            db_ids = [c for c in db_ids if c in related_db_ids]

        # get sibling db subnet group ids.
        subnet_ids = []
        for desc in descriptions:
            if desc["DBInstanceIdentifier"] in db_ids:
                subnet_ids.append(desc["DBSubnetGroup"]["DBSubnetGroupName"])

        for db_id in db_ids:
            # delete the db_instance.
            self.evpc.log.emit("deleting rds: {}".format(db_id))
            if skip_snapshot:
                self.delete_db_instance(
                    DBInstanceIdentifier=db_id, SkipFinalSnapshot=skip_snapshot
                )
            else:
                self.delete_db_instance(
                    DBInstanceIdentifier=db_id,
                    FinalDBSnapshotIdentifier="{}-{}".format(db_id, date),
                )

        # wait for all db_ids to reach db_instance_deleted state.
        self.evpc.log.emit("waiting for rds delete ...")
        self.wait_for_related_dbs("db_instance_deleted", db_ids)

        for subnet_id in subnet_ids:
            # delete the sibling db subnet group.
            self.delete_db_subnet_group(DBSubnetGroupName=subnet_id)

    def reset_master_passwords(self, db_ids):
        """
        Iterate over list of db_ids (names) reset master password immediately.
        Return dictionary of changes in the form of {'db_id' : 'new_pass'}.
        """
        results = {}
        for db_id in db_ids:
            # 16 chars was an arbitrary choice.
            new_password = generate_password(16)
            self.modify_db_instance(
                DBInstanceIdentifier=db_id,
                MasterUserPassword=new_password,
                ApplyImmediately=True,
            )
            results[db_id] = new_password
        return results
