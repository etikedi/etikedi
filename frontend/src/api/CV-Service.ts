import Api from "@/api/api";

export default {
    getCv(params: {cvId: number}): Promise<any> {
        return Api().get("/resumees/" + params.cvId);
    }
};
