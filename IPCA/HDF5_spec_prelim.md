The preliminary specification for the GMRA HDF5 file format is published
on the web in a [Google Doc here](https://docs.google.com/document/d/1h50SPiZSpFG40TA8OfnBAC2E6csVmbTiOt6ltM3FIfo/pub)

This format is also the basis for the IPCA tree data metadata JSON format
we use while still using the sambinary data and label file format.
It's basically a JSON-based config file to specify the file names, 
data types, and any necessary parameter values, such as original
image dimensions if the data is images, or terms associate with term
vectors if the data are from documents.

```
metadata.json
{
  filename: 'ipca.tree',
  dataset_type: 'image',
  image_n_rows: 28,
  image_n_columns: 28,
  labels: {
    digit_id: {
      filename: 'labels.data.hdr',
      description: 'integers 0 and 1 corresponding to actual handwritten digits 1 and 2'
    }
  }
}
```
