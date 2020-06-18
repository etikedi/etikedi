<template>
	<article>
		<header>
			<nav
				class="navbar is-fixed-top hero is-info is-bold"
				role="navigation"
				aria-label="main navigation"
			>
				<div class="hero-foot">
					<div class="container">
						<div id="navbarMenuHeroA" class="navbar-menu">
							<div class="navbar-start">
								<b-button
									class="navbar-item"
									tag="a"
									type="is-link"
									icon-left="chevron-left"
									@click="prevDataset"
									:disabled="prevButtonDisabled"
									inverted
									outlined
								>
									Prev
								</b-button>
								<h2 class="title" style="padding: 0 1rem 0 1rem">
									{{ $store.getters.activeDatasetId }}
								</h2>
								<b-button
									class="navbar-item"
									tag="a"
									type="is-link"
									icon-right="chevron-right"
									@click="nextDataset"
									:disabled="nextButtonDisabled"
									inverted
									outlined
								>
									Next
								</b-button>
							</div>
							<div class="navbar-end">
								<b-button
									v-for="(label, index) in labels"
									:key="index"
									class="navbar-item"
									tag="a"
									type="is-link"
									@click="labelDataset(label)"
									inverted
									outlined
								>
									{{ label }}
								</b-button>
							</div>
						</div>
					</div>
				</div>
			</nav>
		</header>
		<section>
			<!-- here go datasetType views -->
		</section>
	</article>
</template>

<script lang="ts">
import {mapState, mapActions, mapGetters} from "vuex";
import store from "@/store";

import CV from "./components/CV/CV.vue";
import DWTC from "./components/dwtc/DWTC.vue";
import Religious from "@/components/religious/Religious.vue";
import CIFAR from "@/components/CIFAR/CIFAR.vue";

export default {
    name: "LabelView",
    props: {
    },
    computed: {
        ...mapState(["prevButtonDisabled", "nextButtonDisabled"]),
        ...mapGetters(["labels"]),
        datasetId: function() {
			return this.$route.params.datasetId;
		},
        datasetType: function() {
			const ds = this.$store.datasets[this.datasetId];
			if(ds.type){
				// the backend told us the DatasetType to display. Use this.
				return ds.type;
			}
			// guess the dataset type (dumb approach)
			return ds.name.toLowerCase()
		},
    },
    methods: {
        ...mapActions(["nextDataset", "prevDataset", "labelDataset"])
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
