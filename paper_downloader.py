import argparse
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class TypedArgs(argparse.Namespace):
    urls: list[str]
    save_dir: str

    @staticmethod
    def from_argparse(args: argparse.Namespace) -> "TypedArgs":
        return TypedArgs(**vars(args))


class DownloaderBase:
    def download(self, url: str, save_dir: str) -> tuple[str, str, Path]:
        """
        Download a paper from the given URL and save it to the save_dir.
        Args:
            url (str): URL of the paper.
            save_dir (str): Directory to save the downloaded paper.

        Returns:
            tuple[str, str, Path]: URL of the downloaded paper, title of the paper, and the path to the saved paper.
        """
        raise NotImplementedError()


class ACLAnthologyDownloader(DownloaderBase):
    def download(self, url: str, save_dir: str = "./") -> tuple[str, str, Path]:
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        title = soup.find(id="title").text.replace(" ", "_").replace(":", "")
        pdf_url = url + ".pdf"
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f"{title}.pdf"
        with open(save_path, "wb") as f:
            f.write(requests.get(pdf_url).content)

        return pdf_url, title, save_path


class ArXivDownloader(DownloaderBase):
    def download(self, url: str, save_dir: str = "./") -> tuple[str, str, Path]:
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        title = (
            soup.find("h1", class_="title mathjax")
            .text.replace(" ", "_")[6:]
            .replace(":", "")
        )
        pdf_url = url.replace("abs", "pdf")
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f"{title}.pdf"
        with open(save_path, "wb") as f:
            f.write(requests.get(pdf_url).content)


def main(args: TypedArgs):
    urls = args.urls
    if not isinstance(urls, list):
        urls = [urls]

    for i, url in enumerate(urls):
        if url[-1] == "/":
            url = url[:-1]
        parsed_url = urlparse(url)
        if parsed_url.netloc == "aclanthology.org":
            downloader = ACLAnthologyDownloader()
        elif parsed_url.netloc == "arxiv.org":
            downloader = ArXivDownloader()
        else:
            raise NotImplementedError(f"Unsupported URL: {url}")

        downloader.download(url, args.save_dir)
        print(f"Downloaded {i + 1}/{len(urls)} papers.")


parser = argparse.ArgumentParser()
parser.add_argument("urls", type=str, nargs="*", help="URL of the paper.")
parser.add_argument("--save_dir", type=str, default="./pdf/")
args = TypedArgs.from_argparse(parser.parse_args())
main(args)
