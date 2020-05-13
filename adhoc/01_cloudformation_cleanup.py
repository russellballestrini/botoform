ECS_CLUSTER="stage-empire-minion"


def filter_stacks_by_tag(stacks, **kwargs):
    """
    Filter AWS CloudFormation Stack objects using their tags.

    For example, if you wanted all the stage stack objects, you could run:
     
      filter_stacks_by_tag(stacks, environment="stage")
    """
    from botoform.util import make_tag_dict
    _stacks = []
    for stack in stacks:
        stack_tags = make_tag_dict(stack)
        for tag_name, tag_value in kwargs.items():
            if tag_name not in stack_tags or stack_tags[tag_name] != tag_value:
                continue
            _stacks.append(stack)
    return _stacks


def get_ecs_service_arns_from_empire_stacks(stacks):
    """
    Given a list of stacks, find each that define a `Services` output.
    Use the data inside this output to accumulate and return a list
    of ECS Service ARNs managed by Empire (including sharded stacks).
    """
    ecs_service_arns = []
    # iterate over all stacks, and collect ECS Service ARNs from outputs.
    for stack in stacks:
        for output in stack.outputs:
            output_key = output["OutputKey"]
            output_value = output["OutputValue"]
            if output_key == "Services" or "CanaryServices":
                # output_value == a string 
                #    of none or many proc_name1=ARN,proc_name2=ARN pairs separated by a coma.
                # example extry:
                # "my_proc=arn:aws:ecs:us-east-1:1234567890:service/stage-empire-minion/my-service-my_proc-123456789"
                procs = output_value.split(",")
                # we need the ARNs by themselves without the proc_name.
                arns = [p.split("=")[-1] for p in procs]
                ecs_service_arns.extend(arns)
    return ecs_service_arns


# get all the ECS Service Arns currently running in the ECS Cluster.
all_service_arns = evpc.ecs.list_all_service_arns(ECS_CLUSTER)

# get all CloudFormation stacks.
all_stacks = list(evpc.boto.cloudformation.stacks.all())

# filter down to stage's empire app stacks.
empire_app_stacks = filter_stacks_by_tag(all_stacks, environment="stage")

# get every ECS Service ARN that stacker/Empire manages.
empire_service_arns = get_ecs_service_arns_from_empire_stacks(empire_app_stacks)

print(
    "stage has {} empire app stacks with {} ECS Services managed.".format(
        len(empire_app_stacks),
        len(empire_service_arns),
    )
)

# set theory for the win!
# https://docs.python.org/2/library/sets.html#set-objects
orphan_service_arns = set(all_service_arns) - set(empire_service_arns)

for service_arn in orphan_service_arns:
    print(service_arn)

print(
    """The {} ECS Cluster is currently running {} services... 
    so by my estimate we have {} orphaned ECS Service ARNs 
    which I listed above and should likely be deleted.
    """.format(
        ECS_CLUSTER,
        len(all_service_arns),
        len(orphan_service_arns),
    )
)


"""
from time import sleep

for service_arn in orphan_service_arns:
    service_name = service_arn.split("/")[-1]

    print("about to delete: {}".format(service_name))
    print("you have 5 seconds to press ctrl-c to abort.")

    sleep(5)

    # WARNING, if you uncomment this block, this tool will really 
    #          delete services. This block of code is gaurded by 
    #          not one, but two comment types!
    #r = evpc.boto.ecs_client.delete_service(
    #    cluster=ECS_CLUSTER,
    #    service=service_name,
    #    force=True,
    #)

    print(r)

    print("deleted: {}".format(service_name))
"""
