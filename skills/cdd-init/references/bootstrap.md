# Bootstrap decisions

## Required information

- What does the product do, and for whom? What does it explicitly avoid becoming?
- Is there a clear trade-off or boundary to preserve?
- Who is the human accepting norms? Where can the decision and accepted content revision be verified?
- How will the code-producing Lead and evaluating Guardian be separated?
- Which ref supplies accepted sources? State explicitly if a new setup has no such ref yet.

## First acceptance

The Canon starts as DRAFT. When the human accepts it, separately record the norm text's revision, the decision source, and the authorized identity. Writing a username in a file is not authentication. Use environment permissions to prevent the agent from exercising the human's acceptance power on their behalf. Do not present a single platform identity both opening and approving a PR as automatically independent approval.

Load later gate sources from the accepted base ref. CANON, GUARDIAN, ruling, or router changes at PR head do not automatically take effect in the same review. If the initial corpus is small, load all accepted sources; a domain router is optional.

## Existing projects

Read existing AGENTS or CANON files before changing them. An initializer conflict report is not permission to delete or overwrite. Prepare proposed additions as a diff that preserves existing norms. A setup request does not itself accept new product principles.
