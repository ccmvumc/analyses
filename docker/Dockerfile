FROM antsx/antspy

RUN pip install nilearn statsmodels matplotlib

# Install packages needed for fslstats
RUN apt-get update -qq && \
    apt-get install -y \
    libopenblas-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
