Implementation of the backendside API. see #25 and #23 for more references.

### API Endpoints

A quick word to the definition of the semantics on this description, the endpoints are defined by 
```
HTTP METHOD resource/uri/ : response description
```
and in some cases also a response example.

#### Datasets

* `GET /api/datasets` : retrieve all available datasets currently defined, with corresponding ids. 

```JSON 
{
  "datasets": [
    {
      "id": 27138,
      "name": "DWTC"
    },
    {
      "id": 45632,
      "name": "CIFAR"
    }
  ]
}
```

#### Labels

* `GET /api/<dataset_id>/labels` : retrieve all labels corresponding to a data set.

a GET request to `/api/2938271/labels` would yield (assuming e.g CIFAR is under the id 2938271):

```JSON 
{
  "labels": [
       { 
         "name" : "CAT",
         "id": 21829
       },
       { 
         "name" : "DOG",
         "id": 21827
       },
       { 
         "name" : "PROGRAMMER",
         "id": 21828
       }
   ]
}
```

#### Getting data samples and starting the active learning module.

In order to get your first data sample, the active learning module must be running on the server.
To start your instance of the active learning module (@s0106988--tu-dresden.de  please correct me on this / express your opinion) you have to fire a subprocess over an endpoint defined by a request which we have yet to specify.

After doing this, you can start getting your data with:

* `GET /api/<dataset_id>` : returns the first data point to be labeled, as suggested by the AL program.

a possible response, from the DWTC dataset:

```JSON
{
  "datasample": {
       "id" : 29392,
       "data" : "<tbody><tr><span> ... </tbody>"
   }
}
```
**for more information about how your response would look like**, please refer to the model definitions presented [here.](https://gitlab.hrz.tu-chemnitz.de/ddsg/aergia/aergia/issues/2#note_81890)

#### post your labeling results from the user

after the user is done labeling the data, send:

* `POST /api/sample/<datasample_id>` : send the user labeled data as (datasample_id, label_id, user_id), and receive the next to be labeled data sample (from the same dataset as the one defined by the query).

the post request must also include in the request body:

```JSON
{
   "association" :
      {
         "label_id": 17248,
          "user_id": 29488
      }
}

```

a response example, just like above (base64 encoded image this time):


```JSON
{
  "datasample": {
       "id" : 29342,
       "data" : "TWFuIGlzIGRpc3Rpbmd1aXNoZWQsIG5vdCBvbmx5IGJ5IGhpcyByZWFzb24sIGJ1dCBieSB0aGlz
    IHNpbmd1bGFyIHBhc3Npb24gZnJvbSBvdGhlciBhbmltYWxzLCB3aGljaCBpcyBhIGx1c3Qgb2Yg
    dGhlIG1pbmQsIHRoYXQgYnkgYSBwZXJzZXZlcmFuY2Ugb2YgZGVsaWdodCBpbiB0aGUgY29udGlu
    dWVkIGFuZCBpbmRlZmF0aWdhYmxlIGdlbmVyYXRpb24gb2Yga25vd2xlZGdlLCBleGNlZWRzIHRo
    ZSBzaG9ydCB2ZWhlbWVuY2Ugb2YgYW55IGNhcm5hbCBwbGVhc3VyZS4="
   }
}
```

#### Get a specific data sample

you can also request a specific data sample by specifying its id:

* `GET /api/sample/<datasample_id>`


#### User management

still under discussion, see #32 
