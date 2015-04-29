
_codedict()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $( compgen -fW '--suffix --editor --wait --line on off tags edit add link file rollback display' -- $cur) )
    else
        case ${COMP_WORDS[1]} in
            on)
            _codedict_on
        ;;
            off)
            _codedict_off
        ;;
            tags)
            _codedict_tags
        ;;
            edit)
            _codedict_edit
        ;;
            add)
            _codedict_add
        ;;
            link)
            _codedict_link
        ;;
            file)
            _codedict_file
        ;;
            rollback)
            _codedict_rollback
        ;;
            display)
            _codedict_display
        ;;
        esac

    fi
}

_codedict_on()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -W ' ' -- $cur) )
    fi
}

_codedict_off()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -W ' ' -- $cur) )
    fi
}

_codedict_tags()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -fW ' ' -- $cur) )
    fi
}

_codedict_edit()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -fW ' ' -- $cur) )
    fi
}

_codedict_add()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -W ' ' -- $cur) )
    fi
}

_codedict_link()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -fW ' ' -- $cur) )
    fi
}

_codedict_file()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -fW ' ' -- $cur) )
    fi
}

_codedict_rollback()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -eq 2 ]; then
        COMPREPLY=( $( compgen -W ' im' -- $cur) )
    else
        case ${COMP_WORDS[2]} in
            im)
            _codedict_rollback_im
        ;;
        esac

    fi
}

_codedict_rollback_im()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -eq 3 ]; then
        COMPREPLY=( $( compgen -W ' sure' -- $cur) )
    else
        case ${COMP_WORDS[3]} in
            sure)
            _codedict_rollback_im_sure
        ;;
        esac

    fi
}

_codedict_rollback_im_sure()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 4 ]; then
        COMPREPLY=( $( compgen -W ' ' -- $cur) )
    fi
}

_codedict_display()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -fW '-t -l --hline ' -- $cur) )
    fi
}

complete -F _codedict codedict