# Home Depot API Adapter
I am trying to monitor for the lowest price on items like lumber, and sometimes they fluctuate a lot. I created this script that allows for requesting pricing data from Home Depot's hydration API and provide the pricing for items based on store and zipcode.

## Behind the scenes
To pull the item data from the hydration API, you need to POST data to the endpoint requesting details for an item at a particular store and zipcode. Below is a sample JSON POST request to the endpoint. 

```json
{
    "operationName": "productClientOnlyProduct",
    "variables": {
        "skipSpecificationGroup": false,
        "skipSubscribeAndSave": false,
        "skipKPF": false,
        "itemId": "305418731",
        "storeId": "534",
        "zipCode": "77449"
    },
    "query": "query productClientOnlyProduct(.....)"
}
```
We pull the graphql query from the file `query.dat` file, since we're not changing that data on the fly and it's a large amount of data.
