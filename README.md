# personal-site

Fork of [hugo-website-acavar](https://github.com/spoldov/hugo-website-acavar), which is an academic variant of [hugo-website](https://github.com/pmichaillat/hugo-website): dark and minimalist. Built with [Hugo](https://gohugo.io/) from Pascal Michaillat's [hugo-website](https://github.com/pmichaillat/hugo-website) template and the [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme (both MIT; see `LICENSE.md` and `themes/PaperMod/LICENSE`).

It is live at: [speldekamp.github.io/personal-site/about/](https://speldekamp.github.io/personal-site/).

Every push to `main` rebuilds and publishes the site through GitHub Actions (`.github/workflows/hugo.yml`).

## Where things live

| To change | Edit |
| --- | --- |
| Name, role, bio, front-page icons | `config.yml` (`profileMode`) |
| Profile photo | add `static/photo.jpg`, uncomment `imageUrl` in `config.yml` |
| Colours and fonts | `assets/css/extended/custom.css` |
| Icon drawings | `layouts/partials/nav_icon.html` |
| Footer | `layouts/partials/footer.html` |

## Adding content

Copy the example in each section and edit it:

- Paper: `content/papers/example-paper/` (a folder, so the PDF can sit next to `index.md`)
- Dataset: `content/data/dartboard-tool-test.md`
- Course: `content/courses/example-course/`
- Code: `content/code/example-project.md`
- Blog post: `content/blog/first-post.md`
- About page: `content/about.md`
