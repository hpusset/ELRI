<tmx pair = "%s-%s">
    {
        for $tu in //tu[tuv/@xml:lang='%s' and tuv/@xml:lang='%s']
            return
                <tu source='{base-uri($tu)}' last_date_retrieved='{format-date(current-date(), "[Y0001]-[M01]-[D01]")}'>
                    {
                        for $tuv in $tu/tuv
                        return $tuv
                    }
               </tu>
    }
</tmx>