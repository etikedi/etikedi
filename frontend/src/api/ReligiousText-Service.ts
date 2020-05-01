import Api from '@/api/api';

export default {
    /*
    Insert correct API here later, dummy for now
    
    getReligiousText(params: { rtId: number }): Promise<any> {
        return Api().get("/religioustexts/" + params.rtId);
    }
    */
    getReligiousText(params: {rtId: number}): Promise<any> {
        return Promise.resolve(params.rtId.toString());
    }
}