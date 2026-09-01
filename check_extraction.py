import fitz
doc = fitz.open("data/docs/infosys_annual_report.pdf")
print(doc[60].get_text("text")[:1000])