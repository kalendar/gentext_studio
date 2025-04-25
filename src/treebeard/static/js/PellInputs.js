var showdownConverter = new showdown.Converter();
var turndownService = new TurndownService();

var tokenFields = document.querySelectorAll(".pell");

tokenFields.forEach((tokenField) => {
  var editor = pell.init({
    element: tokenField,
    onChange: () => {
      update(tokenField, editor);
    },
    actions: ["bold", "italic", "heading1", "heading2", "olist", "ulist"],
  });

  editor.content.innerHTML = showdownConverter.makeHtml(
    tokenField.dataset.content,
  );

  update(tokenField, editor);
});

function update(tokenField, editor) {
  var markdown = convertToMD(editor.content.innerHTML);
  updateTextArea(`textarea-${tokenField.id}`, markdown);

  var tokenCounter = editor.parentElement.querySelector(".token-count");
  if (tokenCounter !== null) {
    updateTokenCount(tokenCounter, markdown);
  }
}

function updateTokenCount(tokenCounter, content) {
  var words = 0;
  var lines = content.split("\n");
  lines.forEach((line) => {
    line
      .trim()
      .split(" ")
      .forEach((word) => {
        if (word !== "") {
          words++;
        }
      });
  });

  var tokens = Math.ceil(words * 0.75);

  tokenCounter.innerHTML = `Tokens: ${tokens}`;
}

function updateTextArea(textareaId, content) {
  document.getElementById(textareaId).value = content;
}

function convertToMD(content) {
  var markdown = turndownService.turndown(content);
  return markdown.trim();
}
