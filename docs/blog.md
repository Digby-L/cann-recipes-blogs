# Task Instruction
We have a open-sourced gitcode repo. The link is https://gitcode.com/cann/cann-recipes-infer . DO NOT read the full repo, you only need to look at the ./docs/models/ folder, and DO NOT read the information within each file, you only need to know the title of each file. The ./docs/models/ folder is organized by the name of each model and includes all tech report of this repo. Within each model foler, there are markdown files of tech report and also folder of figures linked in markdown files.

We want all docs to be presented in a website. Your task is to design this website for browsing all tech reports. Note create this website only for markdowns in ./docs/models/ . Don't read other things.

## Web Design
1. Create this website that I can open locally (html) and can be deployed to a server for external users later.
2. Color theme: use example.html and example_full.html as your reference of the color and layout design. Fill in functions and
3. Web Nevigate: a nevigation bar vertically on the left to browse different models. This bar can be hidden by clicking on a left arrow on it and reshown with a right arrow. In the bar, categorized in Infer, Train, Embodied Intellegience, Spatial Intellegience. Under each category, organize in alphabetic order of model name (folder name in ./docs/models). Under each model, when click on model name, extend to show different tech reports for this model. Once click on a report, automatically hide the neviagation bar and show the full report in markdown style (style design is in example_full.html).
4. Web Search bar: need a search bar to search for key words in tech report. Place this bar on top right corner of the webpage.
5. Recent report: show the most recent tech reports in blocks; with summary and title shown in the block, pick a photo for this block. 2 or 3 blocks in each row, with max 6 report blocks.
6. Popular report: get most read reports shown on the front page. Pick 4 reports's title. Show this on the top page too.
7. Get to top: provide a button to get to top or bottom directly.
8. Other design: add some icons to be cute and friendly on the webpage to decorate.

## Important
1. for things or design unsure, let me decide (as multiple choice questions) before write or send requests.
2. do not copy the markdowns into this page; use hyperlink and markdown presentation to show the tech reports.

## Outpus
1. Output an index.html file for this website (renamed from recipe_blog.html).
2. Sum up what you do for this website for other agent to be able to recreate similar website. Write it into recipe_blog_skill.md
