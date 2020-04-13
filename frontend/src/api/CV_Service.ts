import Api from '@/api/api'

export default {
    getCv(params) {
        return Api().get('/resumees/' + params.cvId);
    }
}
