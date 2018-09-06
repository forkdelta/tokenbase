on('issues.opened')
  .filter(context => context.payload.issue.body.match(/This is a request to add a new token to tokenbase/))
  .comment(`
  <!-- First contact -->

Thank you for your request, @{{ sender.login }}! We'll review it as soon as we can. In the meanwhile, here's what to expect:

- All communication regarding your request will be posted here. We will not ask you to move conversation to email or a messenger. You can always see all replies on this page.
- Please make sure your request follows the [required format](https://github.com/forkdelta/tokenbase/blob/master/.github/ISSUE_TEMPLATE/add-a-new-token.md) and that the information provided is complete and accurate. This will improve the speed of processing your request greatly.
- Keep an eye on this issue. We will post all follow-up and additional questions here.
- You will receive a notification once your request has been reviewed for completeness and accepted.
- You will receive another notification when the token you requested is about to be added, along with the date when it is added.

Please note:
- Adding a token to ForkDelta Tokenbase **is free**, we do not charge for this service. If you receive any messages asking for payment, do not respond to them.
- We will not send or accept email or direct messages related to token addition requests.
  `);
