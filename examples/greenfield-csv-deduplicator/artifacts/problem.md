# Problem evidence — CSV duplicate cleanup

Status: accepted greenfield pilot evidence.

## Observed problem

Teams regularly receive CSV exports from external systems where logically repeated
records appear more than once. Manual cleanup in spreadsheet tools is slow,
difficult to reproduce and easy to perform inconsistently across repeated exports.

The affected user has a local CSV file and needs a repeatable way to prepare a
cleaned CSV for downstream analysis without sending the file to an external
service.

## Desired outcome

The user can run a local operation repeatedly on equivalent input and obtain a
predictable cleaned file plus enough summary information to understand what was
removed.

## Evidence constraints

- input is a local CSV file;
- duplicate cleanup is needed before downstream analysis;
- local/offline processing is preferred because source exports may contain
  organization-internal data;
- repeatability matters more than interactive spreadsheet editing.

## Unresolved product decisions

Discovery does not decide:

- what makes two rows duplicates;
- whether the user selects key columns or full-row equality is used;
- which duplicate occurrence is retained;
- whether input row order must be preserved;
- behavior for malformed CSV;
- overwrite/output naming behavior;
- exact CLI syntax or exit codes.

Those decisions belong downstream.
