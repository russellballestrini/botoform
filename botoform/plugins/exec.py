import sys


def Exec(args, evpc):
    """
    Accept a Python program on STDIN and execute it.

    The following examples query all active AMI ids from a VPC
    named `dogtest01` in the `development` AWS account profile.

    The first example is best for short one liners, the second is prefered for bigger scripts.

    Usage 1 (echo and pipe)::

     echo "print(set([i.image_id for i in evpc.instances]))" | bf --profile development exec dogtest01

    Usage 2 (redirection)::

     bf --profile development exec dogtest01 < unique_active_amis.py

    Where `unique_active_amis.py` has the following content::

     print(set([i.image_id for i in evpc.instances]))

    In both examples, the output would look something like this::

     set(['ami-33333333', 'ami-55555555', 'ami-99999999', 'ami-77777777'])

    :param args: The parsed arguments and flags from the CLI.
    :param evpc: An instance of :meth:`botoform.enriched.vpc.EnrichedVPC`.
    """
    script = sys.stdin.read()
    exec(script)
