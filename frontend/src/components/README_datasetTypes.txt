
Dataset Types handling in AERGIA
================================

NOTE: With the introduction of the backend API, this has changed fundamentally!

Every dataset in AERGIA has 2 properties assigned to it: apiType and datasetType. These are supposed to be sent by the backend, but as long as this isn't the case they are guessed.

apiType
=======
This determines which API to use to retrieve datasets. Most datasets will use the common AergiaDefaultAPI, which is also used to load available datasets and labels, however it might be necessary for special datasets/AL backends to implement an own API endpoint.

apiType implementations should go into /store/<apiType>. Each apiType uses a namespaced VueX sub-store, and actions and getters are delegated. See the default API which getters and actions need to be implemented. The namespaced submodule must be named "api_<apiType>".

apiType defaults to 'default'.

datasetType
===========
This determines how the samples are rendered. Each datasetType is associated with a view. Due to limitations of the Vue stack, these views can not be dynamically registered.
To add a datasetType with associated view, you must do this:
- in LabelView.vue, import the view class and add it to the components table.
- In the LabelView template, add a v-if clause with your view, with appropriate datasetType=='foo' comparison.

If the apiType is 'default' (which it will be unless you know what you are doing), the current dataset data to be rendered can be obtained by `mapState("api_default", ["currentSample"])`.

A working example which just displays the contents as plain text would be:
<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <span>
                    {{ currentSample }}
                </span>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import {mapState} from "vuex";

export default {
    name: "Plain Text",
    props: {},
    components: {},
    computed: {
        ...mapState("api_default", ["currentSample"])
    },
    methods: {},
};
</script>
