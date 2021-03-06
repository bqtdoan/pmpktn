import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Phần mềm phòng mạch tư",
    version="1.0",
    author="Vương Kiến Thanh",
    author_email="thanhstardust@outlook.com",
    description="Phần mềm phòng mạch tư miễn phí, sử dụng sqlite và wxpython",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)