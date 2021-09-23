# Telemetry

The Stray Command Line Tool collects anononymous usage statistics about general usage of the tool. Participation is optional and you can opt out if you like.

The collected data is very coarse and only includes the commands that are run and the version of the tool. No information is collected about the machine. There is no way in which we can associate the data with any particular user. We also never send any of the data that you process to our servers.

Our servers do not log ip addresses or otherwise try to associate the events to any particular address and the usage data is truly anonymous.

## Why do we collect data?

Telemetry allows us to accurately gauge which features are being used.

Without telemetry, we would have no idea which features of our tool people actually use. The data is simply to inform us which tools are providing value to our users and which ones are not being used. If we see that a tool that isn't being used takes up a lot of our time, we might consider axing it. On the other hand, if a tool which we think is not that great, sees a lot of usage, we can further invest into it's development.

## Opting out

You can opt out of telemetry by setting the `DO_NOT_TRACK` environment variable to any non-empty value in your shell. This can be done by adding:
```
export DO_NOT_TRACK=true
```
to your shell's rc file and sourcing it for the current session. For example, `.bashrc` for Bash or `.zshrc` for zsh.

If you opt out, we won't send any usage events back to us.

