<template>
    <section class="section">
        <div class="container">
            <div style="position: relative;">
                <table class="table" >
					<tr v-for="(control,name) in paramsTypes" :key="name">
						<td> {{ name }} </td>
						<td v-if='control.type == "enum"'>
                            <div class="select">
                                <b-select v-model="params[name]">
                                    <option v-for='(value) in control.values' :key="value" v-value="value"> {{value}} </option>
                                </b-select>
                            </div>
						</td>
						<td v-if='control.type == "intGZ"'>
                            <b-numberinput type="is-info" v-model="params[name]" v-id="name" v-name="name" min="1" step="1" controls-position="compact"/>     <!-- Std color is purple, change with type. "is-info" is the blue from the banner-->
						</td>
                        <td v-if='control.type == "intGreaterMinusOne"'>
                            <b-numberinput type="is-info" v-model="params[name]" v-id="name" v-name="name" min="-1" step="1" controls-position="compact"/>   
						</td>
						<td v-if='control.type == "prob"'>
                            <b-numberinput type="is-info" v-model="params[name]" v-id="name" v-name="name" min="0.0" max="1.0" step="0.01" controls-position="compact"/>
						</td>
						<td v-if='control.type == "half-to-one"'>
                            <b-numberinput type="is-info" v-model="params[name]" v-id="name" v-name="name" min="0.0" max="1.0" step="0.01" controls-position="compact"/>
						</td>
						<td v-if='control.type == "bool"'>
							<b-checkbox type="is-info" v-model="params[name]">{{name}}</b-checkbox>
						</td>
					</tr>
                </table>
                <div class="submit-button">
                    <b-button type="is-info" tag="input" native-type="submit" value="Submit changes"/>
                </div>
                <b-loading
                        :is-full-page="false"
                        :active.sync="loading"
                        :can-cancel="false">
                </b-loading>
            </div>
        </div>
    </section>
</template>

<script lang="ts">
import ALPAramsService from '@/api/ALParams-Service';
import ALParamsService from '@/api/ALParams-Service';
import AppVue from '../../App.vue';

	const paramsTypes = {
		CLASSIFIER: 			{type:"enum", values:["RF", "DT", "SVM", "ANN"]},
		RANDOM_SEED: 			{type:"intGreaterMinusOne"},
		TEST_FRACTION: 			{type:"prob"},
		SAMPLING: 				{type:"enum", values:[
										"random",
										"uncertainty_lc",
										"uncertainty_max_margin",
										"uncertainty_entropy",
								]},
		CLUSTER:				{type:"enum", values:[
										"dummy",
										"random",
										"MostUncertain_lc",
										"MostUncertain_max_margin",
										"MostUncertain_entropy"
								]},
		
		NR_LEARNING_ITERATIONS:		{type:"intGZ"},
		NR_QUERIES_PER_ITERATION:	{type:"intGZ"},
		USER_QUERY_BUDGET_LIMIT:	{type:"intGZ"},
		
		STOPPING_CRITERIA_UNCERTAINTY:	{type:"prob"},
		STOPPING_CRITERIA_STD: 			{type:"prob"},
		STOPPING_CRITERIA_ACC:			{type:"prob"},
		
		MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS:		{type:"prob"},
		
		WITH_UNCERTAINTY_RECOMMENDATION:					{type:"bool"},
		UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD:		{type:"half-to-one"},
		UNCERTAINTY_RECOMMENDATION_RATIO:					{type:"prob"},
		
		WITH_CLUSTER_RECOMMENDATION: 						{type:"bool"},
		CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE:	{type:"prob"},
		CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED:		{type:"prob"},
		
		ALLOW_RECOMMENDATIONS_AFTER_STOP:					{type:"bool"},
		
		WITH_SNUBA_LITE:									{type:"bool"},
		SNUBA_LITE_MINIMUM_HEURISTIC_ACCURACY:				{type:"prob"},
	}

	const alParams = {
		CLASSIFIER: 			"RF",	// ["RF", "DT", "SVM", "ANN"],
		RANDOM_SEED: 			-1,		// [-1, 0,1, … nach oben offen],
		TEST_FRACTION: 			0.5,	//[zwischen 0.0 und 1.0],
		SAMPLING: 				"uncertainty_max_margin",
										//	"random",
										//	"uncertainty_lc",
										//	"uncertainty_max_margin",
										//	"uncertainty_entropy",
		CLUSTER:				"MostUncertain_max_margin",
										//	"dummy",
										//	"random",
										//	"MostUncertain_lc",
										//	"MostUncertain_max_margin",
										//	"MostUncertain_entropy"
		
		NR_LEARNING_ITERATIONS:								200000,	// [1,2, nach oben offen],
		NR_QUERIES_PER_ITERATION:							100,	// [1,2, nach oben offen],
		USER_QUERY_BUDGET_LIMIT:							2000, 	//[1,2, nach oben offen]
		
		STOPPING_CRITERIA_UNCERTAINTY:						0.0,	// [zwischen 0.0 und 1.0],
		STOPPING_CRITERIA_STD: 								0.0,	// [zwischen 0.0 und 1.0],
		STOPPING_CRITERIA_ACC:								0.0,	// [zwischen 0.0 und 1.0],
		
		MINIMUM_TEST_ACCURACY_BEFORE_RECOMMENDATIONS:		0.0, 	//[zwischen 0.0 und 1.0],
		
		WITH_UNCERTAINTY_RECOMMENDATION:					true,
		UNCERTAINTY_RECOMMENDATION_CERTAINTY_THRESHOLD:		0.99,	// [zwischen 0.5 und 1.0]?
		UNCERTAINTY_RECOMMENDATION_RATIO:					0.01, 	// [zwischen 0.0 und 1.0],
		
		WITH_CLUSTER_RECOMMENDATION: 						true,
		CLUSTER_RECOMMENDATION_MINIMUM_CLUSTER_UNITY_SIZE:	0.3,	// [zwischen 0.0 und 1.0],
		CLUSTER_RECOMMENDATION_RATIO_LABELED_UNLABELED:		0.8,	// [zwischen 0.0 und 1.0],
		
		ALLOW_RECOMMENDATIONS_AFTER_STOP:					true,	// [True, False],
		
		WITH_SNUBA_LITE:									false,
		SNUBA_LITE_MINIMUM_HEURISTIC_ACCURACY:				0.5,	// [zwischen 0.0 und 1.0],
	}
    
    export default {
        name: "ALParams",
		data: function() { return {
			paramsTypes: paramsTypes,
            params: alParams,
		}},
        components: {},
        computed: {},
        methods: { 
            setParams: function(newParams) {
                this.params = newParams;
            }
        },
        mounted(): void {
            this.$store.commit('setDatasetType', "none")
            this.$store.commit('toggleIsHomePage', true)
            this.$store.commit('toggleShowFeatureTooltipsSwitch', false)
        },
        beforeMount() {
                ALPAramsService.loadALParams().then((newData) => {
                    this.setParams(newData);
                });
        },
    };
</script>

<style scoped lang="scss">
table {
    width: 100%;
}

@import "../../assets/ALParams.css";

.select:not(.is-multiple):not(.is-loading)::after {
    border-color: #167df0;
}
</style>
