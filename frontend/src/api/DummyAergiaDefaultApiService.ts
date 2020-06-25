
// shit doesn't work!
// Server's API endpoint throws 500's

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

export default {
    getAllDatasets(): Promise<any> {
        return new Promise(resolve => {
            resolve({
                datasets: [
                    {
                        id: 27138,
                        name: "DWTC"
                    },
                    {
                        id: 45632,
                        name: "CIFAR"
                    },
                    {
                        id: 12347,
                        name: "Religious"
                    },
                ]
            });
        });
    },

    getLabels({datasetId}): Promise<any> {
        return new Promise(resolve => {
            resolve({
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
            });
        });
    },

    getSampleById({sampleId}): Promise<any> {
        return new Promise(resolve => {
            resolve({
			  "datasample": {
				   "id" : sampleId,
				   "data" : "Sample gotten by ID " + sampleId
			   }
			});
        });
    },
    
    getNextSample({datasetId}): Promise<any> {
        return new Promise(resolve => {
			const randi = getRandomInt(10000,99999)
            resolve({
			  "datasample": {
				   "id" : randi,
				   "data" : "Sample gotten by GetNextSample " + randi
			   }
			});
        });
    },

    labelSample({
        sampleId,
        labelId,
        userId,
    }): Promise<any> {
        return new Promise(resolve => {
			console.log("DUMMY API Got Label:")
			console.log([
				sampleId,
				labelId,
				userId,
			])
            const randi = getRandomInt(10000,99999)
            resolve({
			  "datasample": {
				   "id" : randi,
				   "data" : "Sample gotten by LabelSample " + randi
			   }
			});
        });
    }
};
