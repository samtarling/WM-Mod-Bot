"""Helper functions for the commands.

Functions/classes here should return text to be sent, rather than
sending directly, unless they handle Discord exceptions.
"""
import inspect
import io
import mwapi
import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import time
import urllib.parse
import discord
from discord.ext.commands import Context, UserInputError, Bot
from discord import File, HTTPException, Message, Embed

JSONDict = Dict[str, Any]
AliasDictData = Dict[Union[str, Tuple[str, ...]], str]
authRegex = r"(@.*?) authenticated as User:(.*)"


async def isDM(message: Message) -> bool:
    """Helper function to see if this message was a DM"""
    return not message.guild


async def isEmbed(message: Message) -> bool:
    """Helper function to see if this message was an Embed"""
    return bool(message.embeds)


async def getUTC() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def getUserBlocks(username: str) -> str:
    centralauthinfo = mwapi.getCentralAuthInfo(username)
    data = json.loads(centralauthinfo)
    blocks = []

    for wiki in data['query']['globaluserinfo']['merged']:
        if 'blocked' in wiki:
            blocks.append(
                [
                    wiki['wiki'],
                    f"{wiki['blocked']['reason']} until {wiki['blocked']['expiry']}"
                ]
            )
    return blocks


def reportBlocks(message: Message, bot: Bot) -> str:
    authMatch = re.findall(authRegex, message.content)
    if authMatch:
        discordUser = authMatch[0][0]
        wikiUser = authMatch[0][1]
        userBlocks = getUserBlocks(wikiUser)
        if userBlocks:
            bot.admin_channel.send('test')

class AliasDict(Dict[str, str]):
    """Create dicts for values that take many aliases (keys).

    When setting a new item, implicitly sets {value: value} as well.
    Will raise a ValueError if the value is already a key.

    Attributes:
      All inherited from `dict`.
    """

    _error_message = "AliasDict values and keys must not overlap."

    def __init__(self,
                 aliases: AliasDictData,
                 value_isnt_alias: Optional[AliasDictData] = None,
                 unaliased: Optional[Set[str]] = None) -> None:
        """Constructs an AliasDict with no uninherited attributes.

        Args:
          aliases:  An AliasDictData of keys and values.  Keys can be
            either strs or tuples thereof.  If a tuple, AliasDict will
            convert this into each member of that tuple having the
            relevant value.  (The tuple itself will not be preserved as
            a key.)  For each value, a {value: value} mapping will also
            be added to the dict.
          value_isnt_alias:  An AliasDictData that is treated the same
            as `aliases`, except that values do not become
            {value: value} mappings.
          unaliased:  A set of strs that will be turned into
            {set item: set item} mappings.

        Raises:
          ValueError if the values and keys overlaps.
        """
        value_isnt_alias = (value_isnt_alias if value_isnt_alias is not None
                            else {})
        unaliased = unaliased if unaliased is not None else set()
        if aliases.keys() & aliases.values() or aliases.keys() & unaliased:
            raise ValueError(self._error_message)
        data = {v: v for v in set(aliases.values()) | unaliased}
        for k, v in aliases.items() | value_isnt_alias.items():
            if isinstance(k, tuple):
                for i in k:
                    data[i] = v
            else:
                data[k] = v
        super().__init__(data)
        # Just here for __repr__ purposes.  Not used otherwise.
        self._aliases = aliases
        self._value_isnt_alias = value_isnt_alias
        self._unaliased = unaliased

    def __repr__(self) -> str:
        return (f"AliasDict({self._aliases!r}, "
                f"value_isnt_alias={self._value_isnt_alias!r}, "
                f"unaliased={self._unaliased!r})")

    def __str__(self) -> str:
        # It makes sense if you (don't) think about it.  -- THK
        return super().__repr__()

    def __setitem__(self, key: str, value: str) -> None:
        if value in self.keys():
            raise ValueError(self._error_message)
        super().__setitem__(key, value)
        super().__setitem__(value, value)


_WIKI_FAMILIES = AliasDict(
    {('w', 'testwiki', 'test2wiki', 'nost', 'nostalgia'): 'wikipedia',
     'wikt': 'wiktionary',
     'b': 'wikibooks',
     ('d', 'testwikidata'): 'wikidata',
     'n': 'wikinews',
     'q': 'wikiquote',
     's': 'wikisource',
     'species': 'wikispecies',
     'v': 'wikiversity',
     'voy': 'wikivoyage'},
    value_isnt_alias={
        ('c', 'commons', 'login', 'm', 'meta', 'metawiki',
         'incubator'): 'wikimedia',
        'mw': 'mediawiki'
    }
)
_WIKI_LANGS = {
    'aa', 'ab', 'ace', 'ady', 'af', 'ak', 'als', 'alt', 'am', 'an', 'ang',
    'ar', 'arc', 'ary', 'arz', 'as', 'ast', 'atj', 'av', 'avk', 'awa', 'ay',
    'az', 'azb', 'ba', 'ban', 'bar', 'bat-smg', 'bcl', 'be', 'be-tarask',
    'be-x-old', 'bg', 'bh', 'bi', 'bjn', 'bm', 'bn', 'bo', 'bpy', 'br', 'bs',
    'bug', 'bxr', 'ca', 'cbk-zam', 'cdo', 'ce', 'ceb', 'ch', 'cho', 'chr',
    'chy', 'ckb', 'co', 'cr', 'crh', 'cs', 'csb', 'cu', 'cv', 'cy', 'da',
    'dag', 'de', 'din', 'diq', 'dsb', 'dty', 'dv', 'dz', 'ee', 'el', 'eml',
    'en', 'eo', 'es', 'et', 'eu', 'ext', 'fa', 'ff', 'fi', 'fiu-vro', 'fj',
    'fo', 'fr', 'frp', 'frr', 'fur', 'fy', 'ga', 'gag', 'gan', 'gcr', 'gd',
    'gl', 'glk', 'gn', 'gom', 'gor', 'got', 'gu', 'gv', 'ha', 'hak', 'haw',
    'he', 'hi', 'hif', 'ho', 'hr', 'hsb', 'ht', 'hu', 'hy', 'hyw', 'hz', 'ia',
    'id', 'ie', 'ig', 'ii', 'ik', 'ilo', 'inh', 'io', 'is', 'it', 'iu', 'ja',
    'jam', 'jbo', 'jv', 'ka', 'kaa', 'kab', 'kbd', 'kbp', 'kg', 'ki', 'kj',
    'kk', 'kl', 'km', 'kn', 'ko', 'koi', 'kr', 'krc', 'ks', 'ksh', 'ku', 'kv',
    'kw', 'ky', 'la', 'lad', 'lb', 'lbe', 'lez', 'lfn', 'lg', 'li', 'lij',
    'lld', 'lmo', 'ln', 'lo', 'lrc', 'lt', 'ltg', 'lv', 'mad', 'mai',
    'map-bms', 'mdf', 'mg', 'mh', 'mhr', 'mi', 'min', 'mk', 'ml', 'mn', 'mni',
    'mnw', 'mo', 'mr', 'mrj', 'ms', 'mt', 'mus', 'mwl', 'my', 'myv', 'mzn',
    'na', 'nah', 'nap', 'nds', 'nds-nl', 'ne', 'new', 'ng', 'nia', 'nl', 'nn',
    'no', 'nov', 'nqo', 'nrm', 'nso', 'nv', 'ny', 'oc', 'olo', 'om', 'or',
    'os', 'pa', 'pag', 'pam', 'pap', 'pcd', 'pdc', 'pfl', 'pi', 'pih', 'pl',
    'pms', 'pnb', 'pnt', 'ps', 'pt', 'qu', 'rm', 'rmy', 'rn', 'ro', 'roa-rup',
    'roa-tara', 'ru', 'rue', 'rw', 'sa', 'sah', 'sat', 'sc', 'scn', 'sco',
    'sd', 'se', 'sg', 'sh', 'shi', 'shn', 'shy', 'si', 'simple', 'sk', 'skr',
    'sl', 'sm', 'smn', 'sn', 'so', 'sq', 'sr', 'srn', 'ss', 'st', 'stq', 'su',
    'sv', 'sw', 'szl', 'szy', 'ta', 'tay', 'tcy', 'te', 'tet', 'tg', 'th',
    'ti', 'tk', 'tl', 'tn', 'to', 'tpi', 'tr', 'trv', 'ts', 'tt', 'tum', 'tw',
    'ty', 'tyv', 'udm', 'ug', 'uk', 'ur', 'uz', 've', 'vec', 'vep', 'vi',
    'vls', 'vo', 'wa', 'war', 'wo', 'wuu', 'xal', 'xh', 'xmf', 'yi', 'yo',
    'yue', 'za', 'zea', 'zh', 'zh-classical', 'zh-min-nan', 'zh-yue', 'zu'
}
_WIKI_PSEUDOLANGS = AliasDict(
    {'c': 'commons',
     ('m', 'metawiki'): 'meta',
     'nost': 'nostalgia'},
    value_isnt_alias={('d', 'wikidata', 'mediawiki', 'species',
                       'wikispecies'): 'www',
                      ('testwiki', 'testwikidata'): 'test',
                      'test2wiki': 'test2'},
    unaliased={'login', 'incubator'}
)
_VALID_PREFIXES = (_WIKI_FAMILIES.keys()
                   | _WIKI_LANGS
                   | _WIKI_PSEUDOLANGS.keys())


def get_comparison(args: str,
                   base_url: str,
                   defaults: Dict[str, str],
                   keywords: Dict[str, str]) -> str:
    """For getting user comparisons from EIA or the Timeline.

    Args:
      args:  A str of user args.
      base_url:  A str of the base URL of the service being used.
      defaults:  A dict of the default params to pass to the URL.
      keywords:  A dict mapping user-facing keywords (keys) to URL
        params (values).  For the user field, which is not specified by
        keyword, use the key 'user'.

    Returns:
      A str of a URL, or, if less than 2 users were specified, a str of
      a request to specify usernames

    Raises:
      UserInputError:  If fewer than two usernames are specified.
    """
    args: List[str] = args.split("#", maxsplit=1)
    usernames = [name.strip() for name in args[0].split("|")]
    if len(usernames) < 2:
        raise UserInputError

    try:
        flags = [flag.split(":", maxsplit=1) for flag in args[1].split("#")]
    except IndexError:
        flagparams = defaults
    else:
        command = inspect.stack()[1].function
        try:
            flagparams = {**defaults,
                          **{keywords[i.strip()]: j.strip() for i, j in flags}}
        except KeyError:
            badflags = [i.strip() for i, _ in flags if i not in defaults]
            return (f"`?{command}` does not accept the following parameter"
                    + "s" * (len(badflags) > 1) + ": "
                    + ", ".join(f"`{flag}`" for flag in badflags)
                    + f". For more information, type `?help {command}`.")
        except ValueError:
            badflags = [i[0].strip() for i in flags if len(i) == 1]
            return (
                "Invalid syntax with the following paramater"
                + "s" * (len(badflags) > 1) + ": "
                + ", ".join(f"`{flag}`" for flag in badflags)
                + ". Remember to include a colon and value after each"
                f"parameter.  For more information, type `?help {command}`."
            )

    return (
        f"<{base_url}"
        + urllib.parse.urlencode(
            [(keywords['user'], name) for name in usernames]
            + list(flagparams.items())
        ) + ">"
    )


def get_page(*,
             base_url: str,
             basepage: str = "",
             subpage: str,
             suffix: str = "") -> str:
    """Get a subpage of a given page.

    Args:
      base_url:  A str that starts the URL.  Defaults to urls.ENWIKI.
      basepage:  A str of a wikipage's base name, URL-encoded, including
        any trailing separator.
      subpage:  A str of a subpage's name.  Since this is provided by
        the end user, we handle URL-encoding for them.
      suffix:  A str of a suffix to put after the subpage, URL-encoded,
        including any leading separator.

    Returns:
      A str of a URL.
    """
    return f"<{base_url}{basepage}{urllib.parse.quote(subpage)}{suffix}>"


# Okay this is kind of hideous, but I can't think of a better way to
# allow the flexibility of `fr:s:User`, `fr:User`, `s:User`, and
# `s:fr:User`. -- THK
def get_wiki_page(*,
                  target: str,
                  basepage: str = "",
                  suffix: str = "",
                  defaults: Tuple[str, str] = ('wikipedia', 'en')) -> str:
    """Calls `get_page` on an arg of format `[wiki:]subpage`.

    If no language and/or family code is provided, will default to those
    defined in `defaults`.

    Args:
      target:  A str of a target subpage with up to one lang prefix and
        up to one family prefix.  Other text appearing before a colon
        will be ignored.
      defaults:  A 2-tuple of (in order) a family code and a language
        code to default to.
      basepage, suffix:  See `get_page` documentation.

    Returns:
      A str of a URL.  See `get_page` documentation.

    Raises:
      A UserInputError if the subpagename is prefixed with more than one
      valid lang code and/or more than one valid family code.
    """
    parts = target.lstrip(':').split(':')
    # Check for text that isn't actually a lang/family code.
    for idx, part in enumerate(parts):
        if part.lower() not in _VALID_PREFIXES:
            subpage = ':'.join(parts[idx:])
            prefixes = [i.lower() for i in parts[:idx]]
            break
    else:
        subpage = parts[-1]
        prefixes = []
    family, lang = defaults

    if len(prefixes) > 2:
        raise UserInputError
    if len(prefixes) == 2:
        # Exactly 1 family code and exactly 1 language code.
        if not all(len(set(prefixes) & s) == 1
                   for s in (_WIKI_FAMILIES.keys(), _WIKI_LANGS)):
            raise UserInputError
        prefixes.sort(key=lambda x: x in _WIKI_FAMILIES)
        # Cases like `?contribs d:fr:User`.
        if prefixes[1] in _WIKI_PSEUDOLANGS:
            raise UserInputError
        family = _WIKI_FAMILIES[prefixes[1]]
        lang = prefixes[0]
    elif prefixes:
        family = _WIKI_FAMILIES.get(prefixes[0], family)
        lang = _WIKI_PSEUDOLANGS.get(
            prefixes[0],
            prefixes[0] if prefixes[0] in _WIKI_LANGS else lang
        )

    return get_page(base_url=f"https://{lang}.{family}.org/wiki/",
                    basepage=basepage, subpage=subpage, suffix=suffix)


async def safesend(ctx: Context,
                   safe: str,
                   dangerous: str,
                   filename: str,
                   is_json: bool = True) -> None:
    """Send a message that could exceed 2,000 characters.

    Use this on any command that:
      1. Sends variable-length text (e.g. JSON) *or*
      2. Can be called an arbitrary number of times in a single message
         (e.g. `?sock`).

    It will first attempt to send `safe` and `dangerous` together, and,
    if  that results in an HTTPException, will instead send `safe` (if
    non-empty) as message and `unsafe` as a file.

    Will place a newline between `safe` and `dangerous` and will
    automatically format any JSON for display in the message as a code
    block.

    Args:
      ctx:  A Context to send to.
      safe:  A portion of the message that is guaranteed to (or is
        extremely unlikely to) exceed 2,000 characters.  This will be
        sent either way.  Can be empty.
      dangerous:  A portion of the message that will be turned into a
        file if the first attempt to send it fails.
      filename:  A name to assign the file constructed from `unsafe`.
      is_json:  If True, `unsafe` will be formatted in a JSON code block
        in the first attempt at sending; if sent as a file it will be a
        .json file rather than the default .txt.
    """
    fenced = f"```json\n{dangerous}```" if is_json else dangerous
    try:
        await ctx.send(f"{safe}\n{fenced}")
    except HTTPException:
        file_ext = 'json' if is_json else 'txt'
        file = File(io.BytesIO(dangerous.encode('utf-8')),
                    filename=f"{filename}.{file_ext}")
        await ctx.send(safe
                       + ("\n[Rest of o" if safe else "[O")
                       + "utput too long to send as message. Sorry.]",
                       file=file)


def trim_dict(base_dict: JSONDict, dict_template: JSONDict) -> JSONDict:
    """Return a subset of base_dict based on the keys of dict_template.

    Works recursively through nested dicts and through dicts that are
    items in nested lists.

    Args:
      base_dict:  A JSONDict.
      dict_template:  A JSONDict whose values are either dummies or
        nested JSONDicts following the same rules.  When defining a
        template subdict for a key that can hold a list of dicts, do not
        wrap the subdict in a 1-item list.

    Returns:
      A JSONDict containining all items from base_dict whose keys were
      also in dict_template, where the same is true of any subdict or
      any list containing subdicts (in which case all subdicts in the
      list are compared to the same subdict of dict_template.)
    """
    trimmed = {k: base_dict[k]
               for k in dict_template.keys() if k in base_dict.keys()}
    for k, v in trimmed.items():
        if isinstance(v, dict):
            trimmed[k] = trim_dict(v, dict_template[k])
        elif isinstance(v, list):
            trimmed[k] = [trim_dict(i, dict_template[k]) for i in v]
    return trimmed