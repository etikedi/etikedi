export const setCv = (state, data) => {
    state.cv = data;
};

export const nextCv = state => {
    if (state.cvId == 1)
        state.prevButtonDisabled = false;
    state.cvId++;
};

export const prevCv = state => {
    if (state.cvId == 2) {
        state.prevButtonDisabled = true;
        state.cvId--;
    } else {
        state.cvId--;
    }
};

export const start_loading = state => {
    state.loading = true;
};

export const end_loading = state => {
    state.loading = false;
};

export const changeLabel = (state, payload) => {
    for (let i = payload.startId; i <= payload.endId; i++) {
        state.cv.features[i][1]['label'] = payload.label;
    }
};

export const toggle_show_feature_tooltips = (state, new_value) => {
    state.display_feature_tooltips = new_value;
};
