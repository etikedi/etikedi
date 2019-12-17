export const setCv = (state, data) => {
    state.cv = data;
}

export const nextCv = state => {
    if (state.cv_id == 1)
        state.prevButtonDisabled = false;
    state.cv_id++;
}

export const prevCv = state => {
    if (state.cv_id == 2) {
        state.prevButtonDisabled = true;
        state.cv_id--;
    } else {
        state.cv_id--;
    }
}
