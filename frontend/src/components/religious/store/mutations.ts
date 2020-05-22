import {LabelPayload, State} from "./models";

export const setRT = (state: State, data: any) => {
    state.religiousText = data;
};

export const nextRT = (state: State) => {
    // The following only makes sense when the ids really would be numbers like 1 to x, but typical ids are more complex and may contain no logic whether they are the first entry or not.
    // if (state.rtId == 1) {
    //     state.prevButtonDisabled = false;
    // }
    state.rtId++;
};

export const prevRT = (state: State) => {
    // The following only makes sense when the ids really would be numbers like 1 to x, but typical ids are more complex and may contain no logic whether they are the first entry or not.
    // if (state.rtId == 2) {
    //     state.prevButtonDisabled = true;
    // }
    state.rtId--;
};

export const changeLabel = (state: State, payload: LabelPayload) => {
    state.religiousText.features["label"] = payload.label;
};
