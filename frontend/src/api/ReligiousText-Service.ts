import Api from '@/api/api';

export default {
    /*
    Insert correct API here later, dummy for now
    
    getReligiousText(params: { rtId: number }): Promise<any> {
        return Api().get("/religioustexts/" + params.rtId);
    }
    */
   
    getReligiousText(params: {rtId: number}): Promise<any> {
        //console.log('gerTeligiousText(' + params.rtId.toString() + ')');
        //console.log(Promise.resolve(params.rtId.toString()).then(function(value) {console.log(value);}));
        return Promise.resolve(params.rtId.toString());
    }
}