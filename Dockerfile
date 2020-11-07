from archlinux/base:latest

RUN pacman -Syyu --noconfirm
RUN pacman-db-upgrade
RUN pacman -S --noconfirm python python-flask sqlite

WORKDIR /app

COPY . /app

EXPOSE 5000

ENTRYPOINT ["flask"]
CMD ["run"]