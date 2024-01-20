from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import QRegularExpression

class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        rules = [
            (r"\bINFO\b", "green"),
            (r"\bDEBUG\b", "yellow"),
            (r"\bERROR\b", "red"),
            (r"\d{4}-\d{2}-\d{2}", "#1E90FF"),
            (r"\d{2}:\d{2}:\d{2}", "#BA55D3"),
        ]
        self.highlightingRules = [(QRegularExpression(pattern), self.createFormat(color)) for pattern, color in rules]

    def createFormat(self, color):
        textFormat = QTextCharFormat()
        textFormat.setForeground(QColor(color))
        return textFormat

    def highlightBlock(self, text):
        for pattern, textFormat in self.highlightingRules:
            matchIterator = pattern.globalMatch(text)
            while matchIterator.hasNext():
                match = matchIterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), textFormat)
