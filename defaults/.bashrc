export PS1="\[\033[1;36m\]\! $\[\033[0m\] "
export PS1="\[\033[1;36m\]\u@\h:\w $\[\033[0m\] "

_bash_log_commands () {
    # https://superuser.com/questions/175799
    [ -n "$COMP_LINE" ] && return  # do nothing if completing
    [[ "$PROMPT_COMMAND" =~ "$BASH_COMMAND" ]] && return # don't cause a preexec for $PROMPT_COMMAND
    local this_command=`HISTTIMEFORMAT= history 1 | sed -e "s/^[ ]*[0-9]*[ ]*//"`;
    echo "$this_command" >> "$BASH_LOG"
}
bash_log_commands () {
    export BASH_LOG="$1"
    trap '_bash_log_commands' DEBUG
}

