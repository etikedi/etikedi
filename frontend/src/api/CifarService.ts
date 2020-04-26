import CifarApi from "@/api/CifarApi";

export default {
    getImage(): Promise<any> {
        return CifarApi().get("/200/300", {responseType: "blob"});
    }
};
