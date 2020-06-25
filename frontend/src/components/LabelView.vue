<template>
	<article>
		<!-- here go datasetType views -->
			<CV v-if="datasetType == 'cv'"/>
			<DWTC v-if="datasetType == 'dwtc'"/>
			<PlainText v-if="datasetType == 'religious'"/>
			<CIFAR v-if="datasetType == 'cifar'"/>
			
			<!-- fallback for dataset type "none" -->
			<section class="section" v-if="datasetType == 'none'">
				<div class="container">
					<div style="position: relative;">
						<span>
							No dataset selected!
						</span>
					</div>
				</div>
			</section>
			
			<b-loading
                    :is-full-page="false"
                    :active.sync="loading"
                    :can-cancel="false"
                >
                </b-loading>
	</article>
</template>

<script lang="ts">
import {mapState, mapActions, mapGetters} from "vuex";
import store from "@/store";

import CV from "@/components/CV/CV.vue";
import DWTC from "@/components/dwtc/DWTC.vue";
import PlainText from "@/components/dst_plaintext/PlainText.vue";
import CIFAR from "@/components/CIFAR/CIFAR.vue";

export default {
    name: "LabelView",
    components: {
		CV,
		DWTC,
		PlainText,
		CIFAR,
	},
    props: {
    },
    computed: {
        ...mapState(["datasets", "activeDatasetId", "activeDataset", "loading", "labels"]),
        ...mapGetters(["datasetType", "sampleShortTitle", "prevButtonDisabled", "nextButtonDisabled"]),
    },
    methods: {
        
    },
    watch: {
		$route: function(to, from) {
			// react to route changes...
			console.log("Route changed - setting activeDatasetId to "+this.$route.params.datasetId)
			this.$store.commit("setActiveDatasetId", this.$route.params.datasetId);
			this.$store.dispatch("updateActiveDataset");
		},
	},
    mounted(): void {
		console.log("mounting LabelView - setting activeDatasetId to "+this.$route.params.datasetId)
		this.$store.commit("setActiveDatasetId", this.$route.params.datasetId);
		this.$store.dispatch("updateActiveDataset");
    },
    beforeDestroy(): void {
		console.log("destroying LabelView - unsetting activeDatasetId")
		this.$store.commit("setActiveDatasetId", null);
	}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
#navbarMenuHeroA {
}

.sticky {
    position: fixed;
    top: 0;
    width: 100%;
}

.sticky + .section {
    padding-top: 3rem;
}
</style>
