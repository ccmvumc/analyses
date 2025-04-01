import logging
import os, shutil

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.image as img 


logger = logging.getLogger('make_pdfpages')


def _add_results_page(pdf, result_dir, subjects, conditions, sources):
    shutil.copyfile(f'{result_dir}/slice_print.png', f'{result_dir}/slice_print.jpg')
    shutil.copyfile(f'{result_dir}/volume_print.png', f'{result_dir}/volume_print.jpg')

    slice_print = os.path.join(result_dir, 'slice_print.jpg')
    volume_print = os.path.join(result_dir, 'volume_print.jpg')

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8.5, 11))

    fig.suptitle(f'{subjects}\n{conditions}\n{sources}')

    _image = img.imread(volume_print)
    axes[0].imshow(_image)
    axes[0].axis('off')

    _image = img.imread(slice_print)
    axes[1].imshow(_image)
    axes[1].axis('off')

    plt.subplots_adjust(left=0.01, top=0.85, right=0.98, bottom=0.01, wspace=0.01, hspace=0.01)

    pdf.savefig(fig)


def make_report(results_dir, filename):
    with PdfPages(filename) as pdf:
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
                    _add_results_page(pdf, _dir, subj, cond, sources)


results_dir = '/OUTPUTS/conn/results/secondlevel/SBC_01'
pdf_name = '/OUTPUTS/report.pdf'
make_report(results_dir, pdf_name)
