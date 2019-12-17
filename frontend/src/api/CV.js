import Api from '@api/api.js'

export default {
    getCvs(params) {
        return Api().get('/resumees/' + params.cv_id);
    }
}
