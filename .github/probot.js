const KNOWN_TEMPLATES = {
  "add-a-new-token": /This is a request to add a new token to tokenbase/,
  "update-token-information": /This is a request to update token information/,
  "user-support": /This is a user support issue/
};

on("issues.opened")
  .filter(
    // Find issues not matching any templates
    context =>
      Object.values(KNOWN_TEMPLATES).filter(template =>
        context.payload.issue.body.match(template)
      ).length === 0
  )
  .comment(contents(".github/probot/no-template.md"))
  .close();

on("issues.opened")
  .filter(context =>
    context.payload.issue.body.match(KNOWN_TEMPLATES["add-a-new-token"])
  )
  .comment(contents(".github/probot/add-a-new-token-first-contact.md"));

on("issues.opened")
  .filter(context =>
    context.payload.issue.body.match(
      KNOWN_TEMPLATES["update-token-information"]
    )
  )
  .assign("freeatnet")
  .comment(
    contents(".github/probot/update-token-information-first-contact.md")
  );

on("issues.opened")
  .filter(context =>
    context.payload.issue.body.match(KNOWN_TEMPLATES["user-support"])
  )
  .assign("freeatnet");
