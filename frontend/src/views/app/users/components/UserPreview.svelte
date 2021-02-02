<script lang="ts">
  import Card from '../../../../ui/Card.svelte'

  export let user
</script>

<Card disabled={!user.is_active}>
  <h2 class="ma0 mb2">
    {user.fullname}
    {#if user.roles === 'admin'}<span class="admin">Admin</span>{/if}
  </h2>
  <div class="flex justify-between">
    <div>
      {user.username}
      <span class="email">
        {user.email}
      </span>
    </div>
    <div class="actions flex items-center">
      <a href={user.id}>
        <ion-icon class="settings" name="cog-outline" />
      </a>
    </div>
  </div>
</Card>

<style>
  .actions > a {
    margin-left: 1em;
  }

  span.admin {
    border: 2px solid var(--clr-primary-light-alt);
    font-weight: normal;
    margin-left: 0.5rem;
    border-radius: var(--round);
    background-color: var(--clr-primary-light);
    padding: 0.25rem;
    font-size: 1rem;
    position: relative;
    top: -0.175em;
  }

  span.email {
    margin-left: 0.5rem;
    padding-left: 0.5rem;
    border-left: 2px solid var(--clr-primary-light);
  }

  ion-icon.settings {
    font-size: 1.5em;
  }
</style>
