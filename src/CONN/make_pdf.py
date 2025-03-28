from datetime import datetime
import logging
import os

from fpdf import FPDF


logger = logging.getLogger('make_pdf')


class MYPDF(FPDF):
    def set_filename(self, filename):
        self.filename = filename
        today = datetime.now().strftime("%Y-%m-%d")
        self.date = today
        self.title = 'Results Report'

    def footer(self):
        self.set_y(-0.35)
        self.set_x(0.5)

        # Write date, title, page number
        self.set_font('helvetica', size=10)
        self.set_text_color(100, 100, 100)
        self.set_draw_color(100, 100, 100)
        self.line(x1=0.2, y1=10.55, x2=8.3, y2=10.55)
        self.cell(w=1, text=self.date)
        self.cell(w=5, align='C', text=self.title)
        self.cell(w=2.5, align='C', text=str(self.page_no()))


def blank_letter():
    p = MYPDF(orientation="P", unit='in', format='letter')
    p.set_top_margin(0.5)
    p.set_left_margin(0.5)
    p.set_right_margin(0.5)
    p.set_auto_page_break(auto=False, margin=0.5)
    return p


def add_results_page(pdf, result_dir, subjects, conditions, sources):
    # Start the page with titles
    pdf.add_page()
    pdf.set_font('helvetica', size=14)
    pdf.cell(w=7.5, h=0.3, align='C', text=subjects)
    pdf.ln(0.3)
    pdf.cell(w=7.5, h=0.3, align='C', text=conditions)
    pdf.ln(0.3)
    pdf.cell(w=7.5, h=0.3, align='C', text=sources)
    pdf.ln(0.3)

    slice_print = os.path.join(result_dir, 'slice_print.png')
    volume_print = os.path.join(result_dir, 'volume_print.png')

    pdf.image(slice_print, x=-0.7, y=1.7, w=8.7)
    pdf.ln()

    pdf.image(volume_print, x=1.8, y=6.0, w=4.7)
    pdf.ln()


def make_report(results_dir, filename):
    # Initialize a new PDF letter size and shaped
    pdf = blank_letter()
    pdf.set_filename(filename)

    for subj in sorted(os.listdir(results_dir)):
        if subj.startswith('.'):
            continue

        for cond in sorted(os.listdir(os.path.join(results_dir, subj))):
            if cond.startswith('.'):
                continue

            for sources in sorted(os.listdir(os.path.join(results_dir, subj, cond))):
                if sources.startswith('.'):
                    continue

                print(f'add_results:{subj}:{cond}:{sources}')
                _dir = os.path.join(results_dir, subj, cond, sources)
                add_results_page(pdf, _dir, subj, cond, sources)

    # Save to file
    logger.debug('saving PDF:{}'.format(pdf.filename))
    try:
        pdf.output(pdf.filename)
    except Exception as err:
        logger.error('error saving PDF:{}:{}'.format(pdf.filename, err))


results_dir = '/OUTPUTS/conn/results/secondlevel/SBC_01'
pdf_name = '/OUTPUTS/report.pdf'
make_report(results_dir, pdf_name)
