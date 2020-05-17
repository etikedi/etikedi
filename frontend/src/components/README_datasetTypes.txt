
Dataset Types handling in AERGIA
================================

AERGIA uses VueX store modules to keep local states for each of the dataset types. The root store is used to save the selected dataset type, and to delegate the actions from the header view.

Responsibility of modules
=========================
The module is fully responsible for
- keeping track of the dataset that is loaded, especially its ID has to be in the module store
- Communicating with the backend, both to retrieve datasets and to submit labels
- Providing the dataset view

AERGIA handles these tasks:
- providing Next, Prev, and label buttons and delegation of actions
- asking the module for available labels and current dataset ID
- Selection of used dataset type

Adding a dataset type
=====================

To add a dataset type, Code has to be inserted in the following places:
1. create a Vue view to display datasets, preferably in /components/<yourdatasettype>/<yourdatasettype>.vue
2. Create a file which exports a state module table (see VueX modules documentation), e.g. something that can be inserted into the "modules" table of a VueX store
   (for the required actions and getters, see below)
3. Import the VueX state module in /store/index.ts and add it to the "modules" table. The module name must equal the internal ID used for your dataset type (e.g. 'cv' for CV's)
4. In /components/Header.vue, add an entry to the dropdown menu
5. In /App.vue, import the view component and add:
	- an entry to the template to show the view when required
	- the view to the "components" table

VueX Store actions and getters
==============================

AERGIA assumes that the following actions are defined in the store module:
- nextDataset: load the next dataset of your type
- prevDataset: load previous
- loadDataset: initially load or reload the current dataset
- labelDataset(payload = label:String): Label the dataset with the clicked label.

The following getters have to be defined:
- activeDatasetId: The ID of the currently loaded dataset. As of now, only used to be displayed in header
- labels: A list of strings which are the available labels to be shown in header, and to be passed to labelDataset.

AERGIA delegates any action and getter requests the header UI does to the module that is selected in the dropdown.

Example
=======
For an example, see the "CV" module (internal ID 'cv')
