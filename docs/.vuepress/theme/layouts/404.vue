<template>
  <div class="theme-container">
    <div class="theme-default-content">
      <h1>404</h1>

      <blockquote>{{ getMsg() }}</blockquote>

      <RouterLink to="/">
        Take me home.
      </RouterLink>
    </div>
  </div>
</template>

<script>
const msgs = [
  `There's nothing here.`,
  `If you really want to find something ...`,
  `Here's a puzzle for you!`,
  `Solve: 106454dd91c9`,
  `Search: RC4-MD5`,
  `Solve: N2J3MjoxOFp0MDhPQzI3eGViZTRVNW9sVHIwZw==`,
  `Search: Base64`,
]

export default {
  methods: {
    getMsg () {
      return msgs[Math.floor(Math.random() * msgs.length)]
    }
  }
}
</script>
