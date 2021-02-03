<script>
  import { Route } from 'tinro'

  import Dashboard from './views/Dashboard.svelte'
  import UserForm from './views/UserForm.svelte'
</script>

<Route path="/">
  <Dashboard />
</Route>
<Route path="/:id">
  <UserForm />
</Route>
