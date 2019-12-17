import CV_service from '@/api/CV_Service';

export const nextCv = ({dispatch, commit}) => {
    commit('nextCv');
    dispatch('loadCv');
}


export const prevCv = ({dispatch, commit}) => {
    commit('prevCv');
    dispatch('loadCv');
}

export const loadCv = ({commit, state}) => {
    return CV_service.getCv({cv_id: state.cv_id}).then(({data}) => {
        commit('setCv', data);
    })
}
