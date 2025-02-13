# Data Flow S3 Importer

> This package helps python and django projects import data exposed by Data Flow into an S3 bucket.

Data Flow is a data pipeline service that can be made to write data into S3 buckets for ingestion by client applications.

This package will use boto to connect to the given bucket, find the right location within the bucket and read the list of files in there.

It will then take a single file and process it line by line, expecting a JSON object with an 'object' key containing a single entity on each line:

```json
...
{"object": {...}}
...
```

It is possible to override the base class for plain python projects, or the subclass for Django projects.

The subclass will process each object into an instance of the given model, which will be saved to the DB.

If the model inherits from the provided `IngestedModel`, any instances not included in the most recent fetch will be flagged as deleted upstream and won't by default appear in the queryset, although they won't be deleted.

## Usage

...
