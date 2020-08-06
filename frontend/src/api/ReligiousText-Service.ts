import Api from "@/api/api";

export default {
    /*
    Insert correct API here later, dummy for now
    
    getReligiousText(params: { rtId: number }): Promise<any> {
        return Api().get("/religioustexts/" + params.rtId);
    }
    */

    getReligiousText(params: {rtId: number}): Promise<any> {
        //console.log('getReligiousText(' + params.rtId.toString() + ')');
        //console.log(Promise.resolve(params.rtId.toString()).then(function(rtId) {console.log(rtId);}));
        return Promise.resolve(params.rtId.toString());
    }
};
