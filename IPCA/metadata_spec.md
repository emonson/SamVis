The preliminary specification for the GMRA HDF5 file format is published
on the web in a [Google Doc here](https://docs.google.com/document/d/1h50SPiZSpFG40TA8OfnBAC2E6csVmbTiOt6ltM3FIfo/pub)

This format is also the basis for the IPCA tree data metadata JSON format
we use while still using the sambinary data and label file format.
It's basically a JSON-based config file to specify the file names, 
data types, and any necessary parameter values, such as original
image dimensions if the data is images, or terms associate with term
vectors if the data are from documents.

Possible values for fields (not all supported, but soon...):

original\_data
- dataset\_type: image [gene, document, ...]
- labels / variable\_type: categorical [continuous]
- labels / data\_type: i, f [s]

```json
data_info.json for MNIST digits example:

{
	"original_data": {
		"description": "MNIST handwritten digits subset of 1000 1s and 2s",
		"url": "",
		"dataset_type": "image",
		"image_n_rows": 28,
		"image_n_columns": 28,
		"labels": {
			"digit_id": {
				"filename": "labels.data.hdr",
				"variable_type": "categorical",
				"data_type": "i",
				"description": "integers 0 and 1 corresponding to actual handwritten digits 1 and 2",
				"key": {
					"0": "digit1",
					"1": "digit2"
				}
			}
		}
	},
	"full_tree": {
		"filename": "tree.ipca"
  }
}

```

```json
data_info.json for gene expression example:

{
	"original_data": {
		"dataset_type": "gene",
		"description": "gene expression data of multiple individuals over 21 genes",
		"url": "",
		"labels": {
			"tissue_id": {
				"filename": "labels.data.hdr",
				"variable_type": "categorical",
				"data_type": "i",
      	"description": "label is an integer 1-9 indicating the tissue type the sample was taken from",
				"key": {
					"1": "tissue1",
					"2": "tissue2",
					"3": "tissue3",
					"4": "tissue4",
					"5": "tissue5",
					"6": "tissue6",
					"7": "tissue7",
					"8": "tissue8",
					"9": "tissue9"
				}
			}
		}
	},
	"full_tree": {
		"filename": "tree.ipca"
  }
}

```
