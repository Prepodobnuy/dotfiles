if status is-interactive
end


set -gx PATH $HOME/.local/bin $PATH

set XDG_PICTURES_DIR "/home/prepodobnuy/.sdc/Documents/Pictures"
set XDG_VIDEOS_DIR "/home/prepodobnuy/.sdc/Documents/Videos"
set XDG_DOWNLOAD_DIR "/home/prepodobnuy/.sdc/Downloads"
set XDG_DOCUMENTS_DIR "/home/prepodobnuy/.sdc/Documents"
set XDG_MUSIC_DIR "/home/prepodobnuy/.sdc/Documents/Music"
set fish_greeting ""


set h ~
set w ~/.sdc/Documents/Wallpapers
set p ~/.sdc/Documents/Projects
set osu ~/.sdb/osu!
set hypr ~/.config/hypr

alias suspend="systemctl suspend"
alias n="fastfetch"
alias p="sudo pacman"
alias pac="sudo pacman"
alias c="clear"
alias cl="clear"
alias l="clear; lsd -la"
alias ls="lsd"
alias xdg="xdg-open"
alias hx="helix"
alias x="helix"
alias nv="helix"
alias v="helix"
