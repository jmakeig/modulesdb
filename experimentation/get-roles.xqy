xquery version "1.0-ml";
(: This probably has to be run as admin in order to do the eval and the sec:* function :)
declare namespace sec="http://marklogic.com/xdmp/security";
declare namespace local="local";
declare function local:get-role-name($role-id) as xs:string {
  xdmp:eval('
  xquery version "1.0-ml";
  import module namespace sec="http://marklogic.com/xdmp/security" at "/MarkLogic/security.xqy";
  sec:get-role-names(' || $role-id || ')', 
  (), 
  <options xmlns="xdmp:eval">
    <database>{xdmp:security-database()}</database>
  </options>)

};

for $perm in xdmp:document-get-permissions("/test4.xqy")
return local:get-role-name($perm/sec:role-id) || ': ' || $perm/sec:capability/data()