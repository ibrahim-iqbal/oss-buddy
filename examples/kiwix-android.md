# example: kiwix/kiwix-android

actual terminal output on 2 Oct 2026, gemma3:4b via ollama.

```

  oss buddy  looking at kiwix/kiwix-android
  pulling readme, tree, issues ...
  7 good-first-issues found
  asking gemma3:4b (running on your laptop)

────────────────────────────────────────────────────────────
Okay, let’s get started!

**PART 1 — What it does**

Kiwix Android is an app that lets you download and read Wikipedia and other content offline. It uses special files called “ZIMs” which are packed archives of web pages, making it possible to access information even without an internet connection.

**PART 2 — Good First Issues**

Here are three issues your friend could tackle this weekend, ranked by difficulty:

1.  **#5141 - Unify toast appearance** - This is a straightforward UI improvement. The goal is to make sure all the little pop-up messages (toasts) in the app look consistent. It would involve reviewing and potentially modifying the code that creates these toasts.
    *   Time Estimate: 2-4 hours
2.  **#5142 - Adding “something” is not UI coherent** - This issue is about adding a new tab to the UI. It seems to be about the user interface of a new tab, ensuring it matches the app's existing design.
    *   Time Estimate: 3-5 hours
3.  **#5078 - Thread-safe date formatting and scope ownership for 2 launches left from #5070** - This seems to be a bug fix related to how dates are handled and potentially memory management within the app.  It's a good introduction to debugging and understanding code flow.
    *   Time Estimate: 6-8 hours

**PART 3 — Where to Start Reading**

Let’s start by looking at the `app/` directory. This is where the core of the Android application is built. Specifically, open the `README.md` file in that directory - it provides a good overview. Also, take a look at `config/` to understand how the app’s settings and data are managed.
────────────────────────────────────────────────────────────

  gemma 3 via ollama. nothing left your machine.

```
