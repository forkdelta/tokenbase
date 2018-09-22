on('issues.opened')
  .filter(context => context.payload.issue.body.match(/This is a request to add a new token to tokenbase/))
  .comment(contents('.github/probot/add-a-new-token-first-contact.md'));
