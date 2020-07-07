import Api from "@/api/api";

export default {
    getCifar(params: {cifarId: number}): Promise<any> {
        return Api().get("/resumees/" + params.cifarId);
    }
};
