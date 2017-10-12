export default  {

    /**
     * Directs the page to a specific ID anchor
     * @see https://stackoverflow.com/questions/13735912/anchor-jumping-by-using-javascript
     * @param  {string} anchorTag id on the page to jump to
     * @return {void}
     */
    jumptToAnchor : function(anchorTag) {
      // is history supported? then use it. otherwise jump manually
      if (history) {
        var url = location.href;               //Save down the URL without hash.
        url = "#"+anchorTag;                 //Go to the target element.
        console.log(url);
        history.replaceState(null,null,url);   //Don't like hashes. Changing it back.
      }
      else {
        var top = document.getElementById(h).offsetTop;
        window.scrollTo(0, top);
      }
    }
}
