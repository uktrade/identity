from typing import Any


PrimaryKey = Any
S3Bucket = Any
S3ObjectSummary = Any


class S3BotoResource:
    class meta:
        class client: ...

    class Bucket[S3Bucket]: ...
